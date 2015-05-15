import curses
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
        Thread(target=self.__renderer_thread, daemon=True).start()
        Thread(target=self.__event_handler_thread, daemon=True).start()

    def __event_handler_thread(self):
        # actions:
        # - exit (curses.endwin())
        # - filter modules
        # - scroll logs
        # - enable/disable autoscroll
        pass

    def __renderer_thread(self):
        self.__init_curses()
        while True:
            sleep(1/self.__REFRESHING_FREQUENCY)
            self.__render_frame()

    def __init_curses(self):
        self.__screen = curses.initscr()  # extract self.__init_curses()
        curses.start_color()
        curses.curs_set(0)

        self.__TIMESTAMP_COLOR = 1
        curses.init_pair(self.__TIMESTAMP_COLOR, curses.COLOR_RED, curses.COLOR_BLACK)
        self.__MODULE_NAME_COLOR = 2
        curses.init_pair(self.__MODULE_NAME_COLOR, curses.COLOR_BLUE, curses.COLOR_BLACK)

        StatisticDataCollector().get_logger().log('system', 'User interface initialized!')

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

    def __render_logs(self, window):
        self.__draw_entitled_box(window, 'Logs')
        window.refresh()

        lines, cols = window.getmaxyx()
        pad = curses.newpad(lines - 2, cols - 2)
        logs = StatisticDataCollector().get_logger().get_logs()
        for timestamp, module_name, message in logs:
            # TODO do logs filtering here! (continue if module_name not in filter list)
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

        # show logs, TODO do scrolling here (currently implemented auto-scrolling only)
        pad_cursor_y, _ = pad.getyx()
        pad_visible_lines = lines - 2
        pad_visible_cols = cols - 2
        autoscroll_position = max(0, pad_cursor_y - pad_visible_lines)
        beg_y, beg_x = window.getbegyx()
        pad.refresh(autoscroll_position, 0, beg_y + 1, beg_x + 1, beg_y + pad_visible_lines, beg_x + pad_visible_cols)

        #test-purposes only - create logs
        import random
        StatisticDataCollector().get_logger().log('test', 'x'*random.randint(50,52)+'y')


    def __render_statistics(self, window):
        self.__draw_entitled_box(window, 'Statistics')
        window.refresh()

    def __draw_entitled_box(self, window, title):
        window.box()
        window.addstr(0, 1, title)

    def __render_info_bar(self, window):
        window.addstr(0, 0, 'infobar')
        window.refresh()
