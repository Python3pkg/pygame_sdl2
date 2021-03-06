#################################### IMPORTS ###################################

if __name__ == '__main__':
    import sys
    import os
    pkg_dir = os.path.split(os.path.abspath(__file__))[0]
    parent_dir, pkg_name = os.path.split(pkg_dir)
    is_pygame_pkg = (pkg_name == 'tests' and
                     os.path.split(parent_dir)[1] == 'pygame')
    if not is_pygame_pkg:
        sys.path.insert(0, parent_dir)
else:
    is_pygame_pkg = __name__.startswith('pygame.tests.')

if is_pygame_pkg:
    from pygame.tests.test_utils import test_not_implemented, unittest
else:
    from test.test_utils import test_not_implemented, unittest
import pygame
from pygame.compat import as_unicode

################################################################################

class EventTypeTest(unittest.TestCase):
    def test_Event(self):
        # __doc__ (as of 2008-08-02) for pygame.event.Event:

          # pygame.event.Event(type, dict): return Event
          # pygame.event.Event(type, **attributes): return Event
          # create a new event object
          # 
          # Creates a new event with the given type. The event is created with
          # the given attributes and values. The attributes can come from a
          # dictionary argument, or as string keys from a dictionary.
          # 
          # The given attributes will be readonly attributes on the new event
          # object itself. These are the only attributes on the Event object,
          # there are no methods attached to Event objects.

        e = pygame.event.Event(pygame.USEREVENT, some_attr=1, other_attr='1')

        self.assertEqual(e.some_attr, 1)
        self.assertEqual(e.other_attr, "1")

        # Event now uses tp_dictoffset and tp_members: request 62
        # on Motherhamster Bugzilla.
        self.assertEqual(e.type, pygame.USEREVENT)
        self.assertTrue(e.dict is e.__dict__)
        e.some_attr = 12
        self.assertEqual(e.some_attr, 12)
        e.new_attr = 15
        self.assertEqual(e.new_attr, 15)

        # For Python 2.x a TypeError is raised for a readonly member;
        # for Python 3.x it is an AttributeError.
        self.assertRaises((TypeError, AttributeError), setattr, e, 'type', 0)
        self.assertRaises((TypeError, AttributeError), setattr, e, 'dict', None)

        # Ensure attributes are visible to dir(), part of the original
        # posted request.
        d = dir(e)
        self.assertTrue('type' in d)
        self.assertTrue('dict' in d)
        self.assertTrue('__dict__' in d)
        self.assertTrue('some_attr' in d)
        self.assertTrue('other_attr' in d)
        self.assertTrue('new_attr' in d)

    def test_as_str(self):
        # Bug reported on Pygame mailing list July 24, 2011:
        # For Python 3.x str(event) to raises an UnicodeEncodeError when
        # an event attribute is a string with a non-ascii character.
        try:
            str(pygame.event.Event(1, a=as_unicode(r"\xed")))
        except UnicodeEncodeError:
            self.fail("Event object raised exception for non-ascii character")
        # Passed.


race_condition_notification = """
This test is dependent on timing. The event queue is cleared in preparation for 
tests. There is a small window where outside events from the OS may have effected
results. Try running the test again.
"""

class EventModuleTest(unittest.TestCase):
    def setUp(self):
        # flush events
        pygame.display.init()
        pygame.event.clear()
        self.assertTrue(not pygame.event.get())

    def tearDown(self):
        pygame.display.quit()

    def test_set_blocked(self):
        # __doc__ (as of 2008-06-25) for pygame.event.set_blocked:
    
          # pygame.event.set_blocked(type): return None
          # pygame.event.set_blocked(typelist): return None
          # pygame.event.set_blocked(None): return None
          # control which events are allowed on the queue
        
        pygame.event.set_blocked(2)

        self.assertTrue(pygame.event.get_blocked(2))

        pygame.event.post(pygame.event.Event(2))

        events = pygame.event.get()
        should_be_blocked = [e for e in events if e.type == 2]
        
        self.assertEqual(should_be_blocked, [])
                
    def test_post__and_poll(self):
        # __doc__ (as of 2008-06-25) for pygame.event.post:

          # pygame.event.post(Event): return None
          # place a new event on the queue

        e1 = pygame.event.Event(pygame.USEREVENT, attr1='attr1')

        pygame.event.post(e1)

        posted_event = pygame.event.poll()
        self.assertEqual (
            e1.attr1, posted_event.attr1, race_condition_notification
        )
        
        # fuzzing event types
        for i in range(1, 11):
            pygame.event.post(pygame.event.Event(i))
            self.assertEqual (
                pygame.event.poll().type, i, race_condition_notification
            )
    def test_post_large_user_event(self):
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'a': "a" * 1024}))

        e = pygame.event.poll()
        self.assertEqual(e.type, pygame.USEREVENT)
        self.assertEqual(e.a, "a" * 1024)



    def test_get(self):
        # __doc__ (as of 2008-06-25) for pygame.event.get:

          # pygame.event.get(): return Eventlist
          # pygame.event.get(type): return Eventlist
          # pygame.event.get(typelist): return Eventlist
          # get events from the queue

        # Put 10 events on the queue
        for _ in range(1, 11):
            pygame.event.post(pygame.event.Event(pygame.USEREVENT))

        self.assertTrue ( len(pygame.event.get()) >= 10 )

    def test_clear(self):

        # __doc__ (as of 2008-06-25) for pygame.event.clear:

          # pygame.event.clear(): return None
          # pygame.event.clear(type): return None
          # pygame.event.clear(typelist): return None
          # remove all events from the queue

        for _ in range(1, 11):
            pygame.event.post(pygame.event.Event(_))
        
        self.assertTrue(pygame.event.poll())  # there are some events on queue

        pygame.event.clear()

        self.assertTrue(not pygame.event.poll(), race_condition_notification)

    def test_event_name(self):

        # __doc__ (as of 2008-06-25) for pygame.event.event_name:

          # pygame.event.event_name(type): return string
          # get the string name from and event id

        self.assertEqual(pygame.event.event_name(2), "KeyDown")
        self.assertEqual(pygame.event.event_name(24), "UserEvent")

    def test_wait(self):
        # __doc__ (as of 2008-06-25) for pygame.event.wait:

          # pygame.event.wait(): return Event
          # wait for a single event from the queue

        pygame.event.post ( pygame.event.Event(2) )
        self.assertTrue(pygame.event.wait())
        
    def test_peek(self):

        # __doc__ (as of 2008-06-25) for pygame.event.peek:

          # pygame.event.peek(type): return bool
          # pygame.event.peek(typelist): return bool
          # test if event types are waiting on the queue

        event_types = [2, 3, 4]

        for event_type in event_types:
            pygame.event.post (
                pygame.event.Event(event_type)
            )
            self.assertTrue(pygame.event.peek(event_type))

        self.assertTrue(pygame.event.peek(event_types))

    def test_set_allowed(self):
        # __doc__ (as of 2008-06-25) for pygame.event.set_allowed:

          # pygame.event.set_allowed(type): return None
          # pygame.event.set_allowed(typelist): return None
          # pygame.event.set_allowed(None): return None
          # control which events are allowed on the queue

        pygame.event.set_blocked(2)
        self.assertTrue(pygame.event.get_blocked(2))
        pygame.event.set_allowed(2)
        self.assertTrue(not pygame.event.get_blocked(2))

    def test_pump(self):
        # __doc__ (as of 2008-06-25) for pygame.event.pump:

          # pygame.event.pump(): return None
          # internally process pygame event handlers
        
        # see it doesn't cause an error
        pygame.event.pump()

    def test_set_grab__and_get_symmetric(self):

        # __doc__ (as of 2008-06-25) for pygame.event.set_grab:

          # pygame.event.set_grab(bool): return None
          # control the sharing of input devices with other applications

        pygame.event.set_grab(True)
        self.assertTrue(pygame.event.get_grab())
        pygame.event.set_grab(False)
        self.assertTrue(not pygame.event.get_grab())

    def test_event_equality(self):
        a = pygame.event.Event(1, a=1)
        b = pygame.event.Event(1, a=1)
        c = pygame.event.Event(2, a=1)
        d = pygame.event.Event(1, a=2)

        self.assertTrue(a == a)
        self.assertFalse(a != a)
        self.assertTrue(a == b)
        self.assertFalse(a != b)
        self.assertTrue(a !=  c)
        self.assertFalse(a == c)
        self.assertTrue(a != d)
        self.assertFalse(a == d)
        
    def todo_test_get_blocked(self):

        # __doc__ (as of 2008-08-02) for pygame.event.get_blocked:

          # pygame.event.get_blocked(type): return bool
          # test if a type of event is blocked from the queue
          # 
          # Returns true if the given event type is blocked from the queue. 

        self.fail() 

    def todo_test_get_grab(self):

        # __doc__ (as of 2008-08-02) for pygame.event.get_grab:

          # pygame.event.get_grab(): return bool
          # test if the program is sharing input devices
          # 
          # Returns true when the input events are grabbed for this application.
          # Use pygame.event.set_grab() to control this state.
          # 

        self.fail() 

    def todo_test_poll(self):

        # __doc__ (as of 2008-08-02) for pygame.event.poll:

          # pygame.event.poll(): return Event
          # get a single event from the queue
          # 
          # Returns a single event from the queue. If the event queue is empty
          # an event of type pygame.NOEVENT will be returned immediately. The
          # returned event is removed from the queue.
          # 

        self.fail() 

################################################################################

if __name__ == '__main__':
    unittest.main()
