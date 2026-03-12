class SemanticNetwork:
    def __init__(self):
        self.relations = []
    def add_relation(self, subject, predicate, obj):
        self.relations.append((subject, predicate, obj))
    def show_relations(self):
        print("Knowledge Base:")
        for s, p, o in self.relations:
            print(f"{p}({s}, {o})")
    def infer(self, entity):
        results = []
        stack = [entity]
        while stack:
            current = stack.pop()
            for s, p, o in self.relations:
                if s == current and p == "is_a":
                    stack.append(o)
                    results.append((current, "is_a", o))
                if s == current and p == "can":
                    results.append((current, "can", o))
        return results
sn = SemanticNetwork()
sn.add_relation("Canary", "is_a", "Bird")
sn.add_relation("Bird", "is_a", "Animal")
sn.add_relation("Bird", "can", "Fly")
sn.add_relation("Tweety", "is_a", "Canary")
sn.show_relations()
print("\nInference for Tweety:")
inferred = sn.infer("Tweety")
for rel in inferred:
    print(f"{rel[1]}({rel[0]}, {rel[2]})")