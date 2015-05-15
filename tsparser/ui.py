import curses
import os
from threading import Thread
from time import sleep

from tsparser.utils import Singleton, StatisticDataCollector


class UserInterface(metaclass=Singleton):
    """
    User Interface is a singleton. Once ran, it renders UI until exiting the app.
    """

    def __init__(self, refreshing_frequency=1):
        self.__REFRESHING_FREQUENCY = refreshing_frequency

    def run(self):
        Thread(target=self.__interface_thread, daemon=True).start()

    def __interface_thread(self):
        self.__init_curses()
        while True:
            sleep(1/self.__REFRESHING_FREQUENCY)
            self.__process_events()
            self.__render_frame()

    def __init_curses(self):
        self.__screen = curses.initscr()
        curses.start_color()
        curses.curs_set(0)
        self.__screen.nodelay(True)
        self.__screen.keypad(True)

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
        self.__scroll_position = self.__auto_scroll_position = 1
        self.__filter_window_active = False
        StatisticDataCollector().get_logger().log('system', 'User interface initialized!')

    def __process_events(self):
        while True:
            key_code = self.__screen.getch()
            if key_code == curses.ERR:
                return
            StatisticDataCollector().get_logger().log('ui', 'got key code: {}'.format(key_code))

            if self.__filter_window_active:
                self.__filter_window_process_event(key_code)
            else:
                self.__main_window_process_event(key_code)

    def __filter_window_process_event(self, key_code):
        if key_code == 27:  # escape
            self.__filter_window_active = False
        elif key_code == ord(' '):
            pass
        elif key_code == curses.KEY_UP:
            pass
        elif key_code == curses.KEY_DOWN:
            pass

    def __main_window_process_event(self, key_code):
        if key_code == curses.KEY_F2:
            self.__logs_auto_scrolling = not self.__logs_auto_scrolling
        elif key_code == curses.KEY_F3:
            self.__filter_window_active = True
        elif key_code == curses.KEY_F9:
            curses.endwin()
            os.kill(os.getpid(), 15)
        elif key_code == curses.KEY_UP:
            self.__logs_auto_scrolling = False
            self.__scroll_position = max(self.__scroll_position - 1, 0)
        elif key_code == curses.KEY_DOWN:
            if self.__scroll_position == self.__auto_scroll_position:
                self.__logs_auto_scrolling = True
            else:
                self.__scroll_position += 1

    def __render_frame(self):
        lines, cols = self.__screen.getmaxyx()
        if lines < 25 or cols < 80:
            self.__screen.clear()
            self.__screen.addstr('Terminal size should be at least 80x25!\n')
            self.__screen.refresh()
            return
        statistics_window_width = 40

        logs_windows = curses.newwin(lines - 1, cols - statistics_window_width, 0, 0)
        self.__render_logs(logs_windows)
        statistics_window = curses.newwin(lines - 1, statistics_window_width, 0, cols - statistics_window_width)
        self.__render_statistics(statistics_window)
        info_bar_window = curses.newwin(1, cols, lines - 1, 0)
        self.__render_info_bar(info_bar_window)
        if self.__filter_window_active:
            width, height = 60, 20
            filter_window = curses.newwin(height, width, (lines - height) // 2, (cols - width) // 2)
            self.__render_filter_window(filter_window)

    def __render_logs(self, window):
        self.__draw_entitled_box(window, 'Logs')
        window.refresh()

        lines, cols = window.getmaxyx()
        pad = curses.newpad(lines - 2, cols - 2)
        logs = StatisticDataCollector().get_logger().get_logs()
        for timestamp, module_name, message in logs:
            # TODO do logs filtering here! (continue if module_name not in filter list)
            # TODO render only what is visible!
            # TODO write this section from scratch! (remember about scroll position and filters!)
            timestamp_str = '{:02}:{:02}:{:02}.{:06}'.format(timestamp.hour, timestamp.minute,
                                                             timestamp.second, timestamp.microsecond)
            module_name = module_name.replace('\n', '<nl>')
            message = message.replace('\n', '<nl>')

            # resizing pad if needed
            pad_lines, pad_cols = pad.getmaxyx()
            whole_message = timestamp_str + ' ' + module_name + ' ' + message + '\n'
            lines_needed = len(whole_message) // pad_cols + 1
            cursor_y, cursor_x = pad.getyx()
            lines_left = pad_lines - cursor_y
            if lines_left < lines_needed + 1:
                pad.resize((pad_lines + lines_needed) * 2, pad_cols)
                pad.move(cursor_y, cursor_x)

            # render line
            pad.addstr(timestamp_str+' ', curses.color_pair(self.__TIMESTAMP_COLOR))
            pad.addstr(module_name+' ', curses.color_pair(self.__MODULE_NAME_COLOR))
            pad.addstr(message)
            if len(whole_message) % pad_cols != 1:
                pad.addstr('\n')

        # show logs
        pad_cursor_y, _ = pad.getyx()
        pad_visible_lines = lines - 2
        pad_visible_cols = cols - 2
        self.__auto_scroll_position = pad_cursor_y
        if self.__logs_auto_scrolling:
            self.__scroll_position = self.__auto_scroll_position
        beg_y, beg_x = window.getbegyx()
        pad.refresh(max(0, self.__scroll_position - pad_visible_lines), 0,
                    beg_y + 1, beg_x + 1, beg_y + pad_visible_lines, beg_x + pad_visible_cols)

        #test-purposes only - create logs # TODO remove it
        import random
        StatisticDataCollector().get_logger().log('test', 'x'*random.randint(50, 52)+'y')

    def __render_statistics(self, window):
        self.__draw_entitled_box(window, 'Statistics')
        sub_win = self.__get_sub_window(window)
        stats_to_display = self.__prepare_stats()
        for name, value in stats_to_display:
            sub_win.addstr('{}: {}\n'.format(name, value))
        window.refresh()

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

    @staticmethod
    def __draw_entitled_box(window, title):
        window.box()
        window.addstr(0, 1, title)

    @staticmethod
    def __get_sub_window(window, margin=1):
        lines, cols = window.getmaxyx()
        beg_y, beg_x = window.getbegyx()
        return window.subwin(lines - margin * 2, cols - margin * 2, beg_y + margin, beg_x + margin)

    def __render_info_bar(self, window):
        info_bar_scheme = (
            ('F2', '{} auto scrolling'.format('Disable' if self.__logs_auto_scrolling else 'Enable')),
            ('F3', 'Filter'),
            ('F9', 'Exit'),
            ('↑↓', 'Scroll')
        )
        for key, description in info_bar_scheme:
            window.addstr(key)
            window.addstr(description, curses.color_pair(self.__INFO_BAR_DESC_COLOR))
        window.refresh()

    def __render_filter_window(self, window):
        window.bkgd(' ', curses.color_pair(self.__FILTER_WINDOW_BACKGROUND))
        self.__draw_entitled_box(window, 'Filter')
        sub_win = self.__get_sub_window(window)
        sub_win.addstr('Please use arrows, space and escape to navigate.\n')
        # TODO implement filtering window logic
        window.refresh()
