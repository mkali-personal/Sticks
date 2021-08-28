class Student:
    def __init__(self
                 ,name
                 ,near_by_students=[]
                 ,eye_contact_students=[]
                 ,preferred_rows=[]
                 ,preferred_columns=[]):
        self.name = name
        self.preferred_rows = preferred_rows
        self.near_by_students = near_by_students
        self.eye_contact_students = eye_contact_students
        self.preferred_columns = preferred_columns
        self.num_of_constraints = None
        self.id = None
        self.seat = None

    def extract_near_by_names(self):
        return [s.name for s in self.near_by_students]

    def extract_eye_contact_names(self):
        return [s.name for s in self.eye_contact_students]

    def extract_rows_names(self, mapper):
        return [x for x in list(mapper.keys()) if mapper[x] in self.preferred_rows]

    def extract_column_names(self, mapper):
        return [x for x in list(mapper.keys()) if mapper[x] in self.preferred_columns]

    def rank_self(self):
        self.num_of_constraints = 24 * len(self.eye_contact_students) + \
                                  6 * len(self.near_by_students) - \
                                  8 * len(self.preferred_columns) - \
                                  8 * len(self.preferred_rows)
