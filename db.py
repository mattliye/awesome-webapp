#db.py

#数据库引擎对象
class _Engine(object):
	def _init_(self, connect):
		self.connect = connect
	def connect(self):
		return self.connect()

engine = None

#持有数据链接的上下文对象：

class _DbCtx(threading.local):
	def _init_(self):
		self.connection = None
		self.transactions = 0

	def is_init(self):
		return not sel.connection is None

	def init(self):
		self.connection = LasyConnection()
		self.transactions = 0

	def cleanup(self):
		self.connection.cleanup()
		self.connection = None

	def cursor(self):
		return self.connection.cursor()

_db_ctx = _DbCtx()


class _ConnectionCtx(object):
	def _enter_(self):
		global _db_ctx
		self.should_cleanup = False
		if not _db_ctx.is_init():
			_db_ctx.init()
			self.should_cleanup = True
		return self

	def _exit_(self, exctype, excvalue, traceback):
		global _db_ctx
		if self.should_cleanup:
			_db_ctx.cleanup()

def connection():
	return _ConnectionCtx()


@with_connection
def select(sql, *args):
    pass

@with_connection
def update(sql, *args):
    pass

@with_transaction
def do_in_transaction():
    pass

class _TransactionCtx(object):
    def __enter__(self):
        global _db_ctx
        self.should_close_conn = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_close_conn = True
        _db_ctx.transactions = _db_ctx.transactions + 1
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        _db_ctx.transactions = _db_ctx.transactions - 1
        try:
            if _db_ctx.transactions==0:
                if exctype is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.should_close_conn:
                _db_ctx.cleanup()

    def commit(self):
        global _db_ctx
        try:
            _db_ctx.connection.commit()
        except:
            _db_ctx.connection.rollback()
            raise

    def rollback(self):
        global _db_ctx
        _db_ctx.connection.rollback()






