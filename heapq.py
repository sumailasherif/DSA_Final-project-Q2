import heapq

heap = []
heapq.heappush(heap, (0, "Curepipe"))     # tuples compare by first element, so (distance, node)
distance, node = heapq.heappop(heap)      # always gives you the smallest distance currently on the heap

