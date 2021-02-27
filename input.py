from queue import SimpleQueue
from tqdm import tqdm

class Simulation(object):
    def __init__(self, fileName):
        self.streets_by_name = dict()
        self.streets_by_dest = dict()
        self.cars = []
        self.load_data(fileName)

    class Intersection(object):
        def __init__(self, id):
            self.id = id
            self.incoming_roads = []
            self.incoming_queues = dict()
            self.schedule = []
            self.green_road = None
        
        def addRoad(self, road):
            self.incoming_roads.append(road)
            self.incoming_queues[road] = SimpleQueue()
        
        def addToQueue(self, road, car):
            self.incoming_queues[road].put(car)

        def processQueue(self):
            if self.green_road is None:
                return
            if self.incoming_queues[self.green_road].empty():
                return
            car = self.incoming_queues[self.green_road].get()
            car.goToNextRoad()
        
        def updateSchedule(self, t):
            if self.schedule == []:
                self.green_road = None
                return
            t = t % len(self.schedule)
            self.green_road = self.schedule[t]

    class Car(object):
        def __init__(self, context, route, id):
            self.context = context
            self.id = id
            self.route = route
            self.current_road = route[0]
            self.road_index = 0
            self.pos_on_road = context.streets_by_name[self.current_road][3]
            self.has_reached = False
            self.context.intersections[self.context.streets_by_name[self.current_road][1]].addToQueue(self.current_road,self)
            self.queued = True
        
        def __str__(self):
            out =  '\nCar Number %d' % self.id
            out += '\nRoute: %s' % self.route
            out += '\nPos: %d on %s' % (self.pos_on_road, self.current_road)
            out += '\nReached?: %s' % ('Yes' if self.has_reached else 'No')
            if self.queued:
                out+= '\nCurrently Queued'
            out += '\n'
            return out
        
        def getCurrentPos(self):
            return self.current_road, self.pos_on_road

        def goToNextRoad(self):
            assert (self.road_index+1 < len(self.route))
            self.road_index += 1
            self.current_road = self.route[self.road_index]
            self.pos_on_road = 0
            self.queued = False

        def advanceByOne(self, t):
            if (self.pos_on_road < self.context.streets_by_name[self.current_road][3]):
                self.pos_on_road += 1
                if self.pos_on_road == self.context.streets_by_name[self.current_road][3]:
                    if self.current_road == self.route[-1]:
                        self.has_reached = True
                        self.reaching_time = t
                    else:
                        self.context.intersections[self.context.streets_by_name[self.current_road][1]].addToQueue(self.current_road,self)
                        self.queued = True
            else:
                assert (self.queued or self.has_reached)

    def load_data(self, file_name):
        f = open(file_name, 'r')
        lines = f.readlines()
        self.duration, self.no_of_intersections, self.no_of_streets, self.no_of_cars, self.score_unit = [int(a) for a in lines[0].strip().split(' ')]
        assert (len(lines) == self.no_of_streets + self.no_of_cars + 1)
        self.intersections = [self.Intersection(i) for i in range(self.no_of_intersections)]
        for street_line in lines[1:1+self.no_of_streets]:
            temp = street_line.strip().split(' ')
            beg,end,name,weight = int(temp[0]), int(temp[1]), temp[2], int(temp[3])
            self.streets_by_name[name] = (beg,end,name,weight)
            self.intersections[end].addRoad(name)
        for i,car_line in enumerate(lines[1+self.no_of_streets:]):
            temp = car_line.strip().split(' ')
            route_length = int(temp[0])
            assert (len(temp) == route_length+1)
            self.cars.append(self.Car(self,temp[1:], i))
        f.close()
    
    def simulate(self):
        for t in tqdm(range(self.duration+1)):

            for i in self.intersections:
                i.updateSchedule(t)

            for c in self.cars:
                c.advanceByOne(t)

            for i in self.intersections:
                i.processQueue()
            # print("At the end of time step %d: " % t)
            # for c in self.cars:
            #    print(c)
        score = 0
        for c in self.cars:
            if c.has_reached:
                score += self.score_unit + (self.duration-c.reaching_time)
        print("Score: %d" % score)
    
    def loadSchedule(self,file_name):
        f = open(file_name,'r')
        line = f.readline()
        a = int(line.strip())
        assert (a>=0 and a<=self.no_of_intersections)
        for _ in range(a):
            line = f.readline()
            e = int(line.strip())
            line = f.readline()
            e_num = int(line.strip())
            for _ in range(e_num):
                line = f.readline()
                temp = line.strip().split(' ')
                road, time = temp[0], int(temp[1])
                for _ in range(time):
                    self.intersections[e].schedule.append(road)
        f.close()
        print("Schedule Loaded")

#input.py
fileName = "f.txt"
solutionName = "f_sol_ext.txt"
s = Simulation(fileName)
s.loadSchedule(solutionName)
s.simulate()