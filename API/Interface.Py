class Interface:
    """
    Public interface layer for SC-OS.
    Defines unified I/O routes so apps, dashboards, youth lab tools,
    or external systems can send instructions into SC-OS.
    """

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def execute(self, request):
        """
        Accept a request from any external system.
        Validate input → forward to orchestration layer → return response.
        """
        if not isinstance(request, dict):
            raise ValueError("Request must be a dictionary")

        # Forward request to the execution manager
        result = self.orchestrator.route(request)
        return result
