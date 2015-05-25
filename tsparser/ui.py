import _curses, curses
from bisect import bisect_left
import math
import os
from threading import Thread
from time import sleep

from tsparser.utils import Singleton, StatisticDataCollector


class UserInterface(metaclass=Singleton):
    """
    User Interface is a singleton. Once ran, it renders UI until exiting the app.
    """

    def __init__(self, refreshing_frequency=30):
        self.__REFRESHING_FREQUENCY = refreshing_frequency

    def run(self):
        Thread(target=self.__interface_thread, daemon=True).start()

    def __interface_thread(self):
        try:
            self.__init_curses()
            while True:
                sleep(1/self.__REFRESHING_FREQUENCY)
                self.__update_filter()
                self.__process_events()
                self.__render_frame()
        except Exception as err:
            error_message = '{}: {}'.format(err.__class__.__name__, err)
            StatisticDataCollector().get_logger().log('ui', error_message)
            curses.endwin()
            print(error_message)

    def __init_curses(self):
        self.__screen = curses.initscr()
        curses.start_color()
        curses.curs_set(0)
        self.__screen.nodelay(True)
        self.__screen.keypad(True)
        self.__SCREEN_MINIMAL_SIZE = 24, 80  # lines, cols

        self.__TIMESTAMP_COLOR = 1
        curses.init_pair(self.__TIMESTAMP_COLOR, curses.COLOR_RED, curses.COLOR_BLACK)
        self.__MODULE_NAME_COLOR = 2
        curses.init_pair(self.__MODULE_NAME_COLOR, curses.COLOR_BLUE, curses.COLOR_BLACK)
        self.__INFO_BAR_DESC_COLOR = 3
        curses.init_pair(self.__INFO_BAR_DESC_COLOR, curses.COLOR_BLACK, curses.COLOR_CYAN)
        self.__FILTER_WINDOW_BACKGROUND = 4
        curses.init_pair(self.__FILTER_WINDOW_BACKGROUND, curses.COLOR_WHITE, curses.COLOR_BLUE)
        self.__FILTER_WINDOW_SELECTION = 5
        curses.init_pair(self.__FILTER_WINDOW_SELECTION, curses.COLOR_BLACK, curses.COLOR_CYAN)

        self.__logs_auto_scrolling = True
        self.__scroll_position = 0
        self.__log_index_to_last_line_no = list()
        self.__cached_processed_logs = list()
        self.__filter_window_active = False
        self.__filter = dict()
        self.__filter_selected_index = int()
        self.__filter_selected_module = str()
        StatisticDataCollector().get_logger().log('ui', 'User interface initialized!')

    def __update_filter(self):
        for module_name in StatisticDataCollector().get_logger().get_all_modules():
            if module_name not in self.__filter:
                self.__filter[module_name] = True

    def __process_events(self):
        while True:
            key_code = self.__screen.getch()
            if key_code == curses.ERR:
                return
            if key_code == curses.KEY_RESIZE:
                self.__delete_cached_logs()
                continue

            if self.__filter_window_active:
                self.__filter_window_process_event(key_code)
            else:
                self.__main_window_process_event(key_code)

    def __delete_cached_logs(self):
        self.__cached_processed_logs.clear()
        self.__log_index_to_last_line_no.clear()

    def __filter_window_process_event(self, key_code):
        if key_code == 27:  # escape
            self.__filter_window_active = False
        elif key_code == ord(' '):
            if self.__filter:
                self.__filter[self.__filter_selected_module] = not self.__filter[self.__filter_selected_module]
                self.__auto_scroll_position = True
                self.__delete_cached_logs()
        elif key_code == curses.KEY_UP:
            self.__filter_selected_index -= 1
            if self.__filter_selected_index == -1:
                self.__filter_selected_index = len(self.__filter) - 1
        elif key_code == curses.KEY_DOWN:
            self.__filter_selected_index += 1
            if self.__filter_selected_index == len(self.__filter):
                self.__filter_selected_index = 0

    def __main_window_process_event(self, key_code):
        if key_code == curses.KEY_F2:
            self.__logs_auto_scrolling = not self.__logs_auto_scrolling
        elif key_code == curses.KEY_F3:
            self.__filter_window_active = True
            self.__filter_selected_index = 0
        elif key_code == curses.KEY_F4:
            StatisticDataCollector().get_logger().clear_logs()
            self.__delete_cached_logs()
        elif key_code == curses.KEY_F9:
            curses.endwin()
            os.kill(os.getpid(), 15)
        elif key_code == curses.KEY_UP:
            self.__logs_auto_scrolling = False
            self.__scroll_position -= 1  # renderer will increase value if it is too small
        elif key_code == curses.KEY_DOWN:
            if self.__cached_processed_logs:
                if self.__scroll_position >= self.__log_index_to_last_line_no[-1]:
                    self.__logs_auto_scrolling = True
                else:
                    self.__scroll_position += 1

    def __render_frame(self):
        lines, cols = self.__screen.getmaxyx()
        min_lines, min_cols = self.__SCREEN_MINIMAL_SIZE
        if lines < min_lines or cols < min_cols:
            self.__screen.clear()
            self.__screen.addstr('Terminal size should be at least {}x{}!\n'.format(min_cols, min_lines))
            self.__screen.refresh()
            return
        statistics_window_width = 40

        logs_windows = self.__screen.subwin(lines - 1, cols - statistics_window_width, 0, 0)
        self.__render_logs_window(logs_windows)
        statistics_window = self.__screen.subwin(lines - 1, statistics_window_width, 0, cols - statistics_window_width)
        self.__render_statistics_window(statistics_window)
        info_bar_window = self.__screen.subwin(1, cols, lines - 1, 0)
        self.__render_info_bar(info_bar_window)
        if self.__filter_window_active:
            width, height = 60, 20
            filter_window = self.__screen.subwin(height, width, (lines - height) // 2, (cols - width) // 2)
            self.__render_filter_window(filter_window)
        self.__screen.refresh()

    def __render_logs_window(self, window):
        window.clear()
        self.__draw_entitled_box(window, 'Logs')

        sub_win = self.__get_sub_window(window)
        lines, cols = sub_win.getmaxyx()
        selected_modules = [module_name for module_name in self.__filter if self.__filter[module_name]]
        logs = StatisticDataCollector().get_logger().get_logs(selected_modules)
        new_logs = logs[len(self.__cached_processed_logs):]
        self.__cache_new_log_entries(new_logs, cols)
        self.__render_visible_log_entries(sub_win)

    def __cache_new_log_entries(self, new_entries, line_width):
        for timestamp, module_name, message in new_entries:
            timestamp_str = '{:02}:{:02}:{:02}.{:06}'.format(timestamp.hour, timestamp.minute,
                                                             timestamp.second, timestamp.microsecond)
            module_name = module_name.replace('\n', '<nl> ')
            self.__cached_processed_logs.append((timestamp_str, module_name, message))
            whole_message = timestamp_str + ' ' + module_name + ' ' + message
            lines_needed = 0
            for pseudo_line in whole_message.split('\n')[:-1]:
                pseudo_line += '\n'
                lines_needed += math.ceil(len(pseudo_line) / line_width)
            lines_needed += math.ceil(len(whole_message.split('\n')[-1]) / line_width)
            previous_entry_last_line = self.__log_index_to_last_line_no[-1] if self.__log_index_to_last_line_no else -1
            self.__log_index_to_last_line_no.append(previous_entry_last_line + lines_needed)

    def __render_visible_log_entries(self, window):
        lines, cols = window.getmaxyx()
        lines -= 1  # last line should be empty (cursor will be there)
                    # otherwise cursor will land below the window (what causes curses error)
        if not self.__cached_processed_logs:
            window.addstr(lines, 0, '(no logs)', curses.A_DIM)
            return
        if self.__logs_auto_scrolling:
            self.__scroll_position = self.__log_index_to_last_line_no[-1]
        self.__scroll_position = max(self.__scroll_position, lines - 1)
        first_line_no = max(0, self.__scroll_position - lines + 1)
        first_log_entry_index = bisect_left(self.__log_index_to_last_line_no, first_line_no)
        log_entry_index = first_log_entry_index
        while log_entry_index < len(self.__cached_processed_logs):
            last_entry_line_no = self.__log_index_to_last_line_no[log_entry_index]
            first_entry_line_no = self.__log_index_to_last_line_no[log_entry_index-1] + 1 if log_entry_index > 0 else 0
            self.__render_log_entry(window, log_entry_index,
                                    max(0, first_line_no - first_entry_line_no),
                                    max(0, last_entry_line_no - self.__scroll_position))

            log_entry_index += 1
            if last_entry_line_no >= self.__scroll_position:
                break

        if self.__scroll_position >= self.__log_index_to_last_line_no[-1]:
            info_message = '(end)'
        else:
            left_lines_count = self.__log_index_to_last_line_no[-1] - self.__scroll_position
            left_lines_count = str(left_lines_count) if left_lines_count < 10**9 else '>=10e9'
            info_message = '({} more lines)'.format(left_lines_count)
        window.addstr(lines, 0, info_message, curses.A_DIM)

    def __render_log_entry(self, window, log_entry_index, omitted_first_lines, omitted_last_lines):
        lines, cols = window.getmaxyx()
        timestamp_str, module_name, message = self.__cached_processed_logs[log_entry_index]
        colored_prefix = timestamp_str + ' ' + module_name + ' '
        whole_message = colored_prefix + message
        entry_lines = list()
        while len(whole_message) > 0:
            next_new_line = whole_message.find('\n') + 1
            if next_new_line == 0:
                next_new_line = cols
            split_point = min(cols, len(whole_message), next_new_line)
            entry_lines.append(whole_message[:split_point])
            whole_message = whole_message[split_point:]
            if len(entry_lines[-1]) < cols and not entry_lines[-1].endswith('\n'):
                    entry_lines[-1] += '\n'
        if omitted_first_lines + omitted_last_lines >= len(entry_lines):
            return

        if omitted_first_lines == 0:
            if len(colored_prefix) <= cols:
                rest_of_first_line = entry_lines[0][len(colored_prefix):]
                window.addstr(timestamp_str + ' ', curses.color_pair(self.__TIMESTAMP_COLOR))
                window.addstr(module_name + ' ', curses.color_pair(self.__MODULE_NAME_COLOR))
                window.addstr(rest_of_first_line)
            else:
                window.addstr(entry_lines[0])
        entry_lines = entry_lines[max(1, omitted_first_lines):len(entry_lines)-omitted_last_lines]
        for line in entry_lines:
            window.addstr(line)

    def __render_statistics_window(self, window):
        window.clear()
        self.__draw_entitled_box(window, 'Statistics')
        sub_win = self.__get_sub_window(window)
        stats_to_display = self.__prepare_stats()
        for name, value in stats_to_display:
            sub_win.addstr('{}: {}\n'.format(name, value))
        self.__render_progress_window(window)

    @staticmethod
    def __prepare_stats():
        def timedelta_to_str(timedelta_obj):
            seconds = timedelta_obj.total_seconds()
            if seconds < 1:
                return '<1 sec'
            seconds = int(seconds)
            result = '{} sec'.format(seconds % 60)
            if seconds >= 60:
                result = '{} min {}'.format(seconds // 60, result)
            return result

        def data_amount_to_str(data_amount):
            steps = (
                (1, 'B'),
                (10**3, 'kB'),
                (10**6, 'MB'),
                (10**9, 'GB')
            )
            last_good_result = '0 B'
            for bound, unit in steps:
                if data_amount < bound:
                    return last_good_result
                last_good_result = '{:.3f} {}'.format(data_amount / bound, unit)
            return last_good_result

        sdc = StatisticDataCollector()
        stats_scheme = (
            ('Time since last receiving', timedelta_to_str(sdc.get_time_since_last_data_receiving())),
            ('Time since start', timedelta_to_str(sdc.get_time_since_start())),
            ('Data receiving speed', data_amount_to_str(sdc.get_data_receiving_speed())+'/s'),
            ('Total data received', data_amount_to_str(sdc.get_total_data_received())),
            ('Queued requests', str(sdc.get_count_of_queued_requests())),
            ('Total sent requests', str(sdc.get_total_count_of_sent_requests()))
        )
        return stats_scheme

    def __render_progress_window(self, window):
        sdc = StatisticDataCollector()
        progress = sdc.get_progress()
        title = sdc.get_progress_title()
        subtitle = sdc.get_progress_subtitle()

        if progress == -1:
            return

        # Create progress window
        lines, cols = window.getmaxyx()
        beg_y, beg_x = window.getbegyx()
        progress_win = window.subwin(beg_y + lines - 5, beg_x)
        self.__draw_entitled_box(progress_win, 'Progress',
                                 0, 0, 0, 0, curses.ACS_SSSB, curses.ACS_SBSS)

        # Subwindow
        sub_win = self.__get_sub_window(progress_win)
        lines, cols = sub_win.getmaxyx()

        # Draw window content
        sub_win.insstr(0, int(cols / 2 - len(title) / 2), title)
        self.__draw_progress_bar(progress, sub_win, 1, cols)
        sub_win.insstr(2, int(cols / 2 - len(subtitle) / 2), subtitle)

    @staticmethod
    def __draw_progress_bar(progress, window, y, width):
        progress_str = '{}%'.format(progress)
        s = ' ' * width
        x_pos = int(width / 2 - len(progress_str) / 2)
        s = s[:x_pos] + progress_str + s[x_pos:]

        for i in range(width):
            fill = i / width < progress / 100
            window.insch(y, i, s[i],
                          curses.A_REVERSE if fill else curses.A_NORMAL)

    @staticmethod
    def __draw_entitled_box(window, title, *border_args):
        window.border(*border_args)
        window.addstr(0, 1, title)

    @staticmethod
    def __get_sub_window(window, margin=1):
        lines, cols = window.getmaxyx()
        beg_y, beg_x = window.getbegyx()
        return window.subwin(lines - margin * 2, cols - margin * 2, beg_y + margin, beg_x + margin)

    def __render_info_bar(self, window):
        window.clear()
        info_bar_scheme = (
            ('F2', '{} auto scrolling'.format('Disable' if self.__logs_auto_scrolling else 'Enable')),
            ('F3', 'Filter'),
            ('F4', 'Clear'),
            ('F9', 'Exit'),
            ('↑↓', 'Scroll')
        )
        for key, description in info_bar_scheme:
            window.addstr(key)
            window.addstr(description, curses.color_pair(self.__INFO_BAR_DESC_COLOR))

    def __render_filter_window(self, window):
        window.clear()
        window.bkgd(' ', curses.color_pair(self.__FILTER_WINDOW_BACKGROUND))
        self.__draw_entitled_box(window, 'Filter')
        sub_win = self.__get_sub_window(window)
        sub_win.addstr('Please use arrows, space and escape to navigate.\n\n')
        self.__render_filter_list(sub_win)

    def __render_filter_list(self, window):
        lines, cols = window.getmaxyx()
        for i, (module_name, is_checked) in enumerate(self.__filter.items()):
            color = self.__FILTER_WINDOW_BACKGROUND
            is_entry_selected = self.__filter_selected_index == i
            if is_entry_selected:
                color = self.__FILTER_WINDOW_SELECTION
                self.__filter_selected_module = module_name

            prefix = '[x] ' if is_checked else '[ ] '
            module_name_needed_length = cols - len(prefix)
            if len(module_name) > module_name_needed_length:
                module_name = module_name[:module_name_needed_length-3] + '...'
            else:
                module_name += ' ' * (module_name_needed_length - len(module_name))
            try:  # TODO if there are many modules (False on May 18th, 2015), implement scrolling for this window
                window.addstr(prefix + module_name, curses.color_pair(color))
            except _curses.error:
                break
