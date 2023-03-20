class TaskSenderInterface:
    def __call__(self, **kwargs) -> str:
        raise NotImplementedError()
