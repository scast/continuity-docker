from collections import defaultdict

class ImageManager(object):
    def __init__(self, images):
        self.images = images

    def build_downward_tree(self, env):
        '''Recursively builds a tree from the image description which points
        downward instead of upwards'''

        self.visit.add(env)
        dep = self.images[env].get('depends', None)

        if dep is not None:
            if env not in self.inverted_tree[dep]:
                self.inverted_tree[dep].append(env)

            if dep not in self.visit:
                self.build_downward_tree(dep)

    @property
    def downward_tree(self):
        '''Returns a downward pointing tree of dependencies between images.'''
        if not hasattr(self, 'inverted_tree'):
            self.visit = set()
            self.inverted_tree = defaultdict(list)

            for env in self.images:
                self.build_downward_tree(env)

        return self.inverted_tree

    def check_for_rebuild(self, root='common', changed_files=[],
                          force=False):
        '''Returns a generator of leaves that must be rebuilt.'''
        q = [root]
        changed_files = set(changed_files)
        needs_rebuilding = set()
        # self.visit = set()

        while q:
            env = q.pop(0)
            parent = self.images[env].get('depends', None)
            watched_files = set(self.images[env]['watch'])

            # if my parent is marked for rebuild, so I am.
            if parent in needs_rebuilding:
                needs_rebuilding.add(env)

            # if some of my watched files changed, I must be rebuilt.
            if changed_files & watched_files:
                needs_rebuilding.add(env)


            # If I'm a leaf, just rebuild my chain up to the one who
            # started it.
            if not self.downward_tree[env] and \
               (env in needs_rebuilding or force):
                yield (env, needs_rebuilding)


            for next_env in self.downward_tree[env]:
                q.append(next_env)

    def gather_dependencies(self, env, needs_rebuilding, force=False):
        '''Gather the dependency chain for this environment.'''
        if env in self.dep_visit:
            return

        if env not in needs_rebuilding:
            if not force:
                return

        current_image = self.images[env]
        parent = current_image.get('depends', None)
        if parent is not None:
            for dep in self.gather_dependencies(parent,
                                                needs_rebuilding,
                                                force=force):
                yield dep

        yield env
        self.dep_visit.add(env)


    def get_rebuild_steps(self, root, changed_files, force=False):
        '''Returns a list of environment that must be rebuilt, in order'''
        self.dep_visit = set()
        for leaf, needs_rebuilding in self.check_for_rebuild(root,
                                                             changed_files,
                                                             force=force):
            for step in self.gather_dependencies(leaf, needs_rebuilding,
                                                 force=force):
                yield step
