from fast_tmp.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator
from tests.base import BaseSite
from tests.testmodels import Address, Event, Reporter, Team, Tournament


class TestPydantic(BaseSite):
    async def asyncSetUp(self) -> None:
        await super(TestPydantic, self).asyncSetUp()
        self.Event_Pydantic = pydantic_model_creator(Event)
        self.Event_Pydantic_List = pydantic_queryset_creator(Event)
        self.Tournament_Pydantic = pydantic_model_creator(Tournament)
        self.Team_Pydantic = pydantic_model_creator(Team)
        self.Address_Pydantic = pydantic_model_creator(Address)

        class PydanticMetaOverride:
            backward_relations = False

        self.Event_Pydantic_non_backward = pydantic_model_creator(
            Event, meta_override=PydanticMetaOverride, name="Event_non_backward"
        )

        self.tournament = await Tournament.create(name="New Tournament")
        self.reporter = await Reporter.create(name="The Reporter")
        self.event = await Event.create(
            name="Test", tournament=self.tournament, reporter=self.reporter
        )
        self.event2 = await Event.create(name="Test2", tournament=self.tournament)
        self.address = await Address.create(city="Santa Monica", street="Ocean", event=self.event)
        self.team1 = await Team.create(name="Onesies")
        self.team2 = await Team.create(name="T-Shirts")
        await self.event.participants.add(self.team1, self.team2)
        await self.event2.participants.add(self.team1, self.team2)
        self.maxDiff = None

    def test_event_schema(self):
        self.assertEqual(
            self.Event_Pydantic.schema(),
            {
                "title": "Event",
                "description": "Events on the calendar",
                "type": "object",
                "properties": {
                    "event_id": {
                        "title": "Event Id",
                        "minimum": 1,
                        "maximum": 9223372036854775807,
                        "type": "integer",
                    },
                    "name": {"title": "Name", "description": "The name", "type": "string"},
                    "tournament": {
                        "title": "Tournament",
                        "allOf": [{"$ref": "#/definitions/tests.testmodels.Event.tournament"}],
                    },
                    "reporter": {
                        "title": "Reporter",
                        "nullable": True,
                        "allOf": [{"$ref": "#/definitions/tests.testmodels.Event.reporter"}],
                    },
                    "participants": {
                        "title": "Participants",
                        "type": "array",
                        "items": {"$ref": "#/definitions/tests.testmodels.Event.participants"},
                    },
                    "modified": {
                        "title": "Modified",
                        "readOnly": True,
                        "type": "string",
                        "format": "date-time",
                    },
                    "token": {"title": "Token", "type": "string"},
                    "alias": {
                        "title": "Alias",
                        "minimum": -2147483648,
                        "maximum": 2147483647,
                        "nullable": True,
                        "type": "integer",
                    },
                    "address": {
                        "title": "Address",
                        "nullable": True,
                        "allOf": [{"$ref": "#/definitions/tests.testmodels.Event.address"}],
                    },
                },
                "required": ["event_id", "name", "tournament", "participants", "modified"],
                "additionalProperties": False,
                "definitions": {
                    "tests.testmodels.Event.tournament": {
                        "title": "tests.testmodels.Event.tournament",
                        "type": "object",
                        "properties": {
                            "id": {
                                "title": "Id",
                                "minimum": 1,
                                "maximum": 32767,
                                "type": "integer",
                            },
                            "name": {"title": "Name", "maxLength": 255, "type": "string"},
                            "desc": {"title": "Desc", "nullable": True, "type": "string"},
                            "created": {
                                "title": "Created",
                                "readOnly": True,
                                "type": "string",
                                "format": "date-time",
                            },
                        },
                        "required": ["id", "name", "created"],
                        "additionalProperties": False,
                    },
                    "tests.testmodels.Event.reporter": {
                        "title": "tests.testmodels.Event.reporter",
                        "description": "Whom is assigned as the reporter",
                        "type": "object",
                        "properties": {
                            "id": {
                                "title": "Id",
                                "minimum": 1,
                                "maximum": 2147483647,
                                "type": "integer",
                            },
                            "name": {"title": "Name", "type": "string"},
                        },
                        "required": ["id", "name"],
                        "additionalProperties": False,
                    },
                    "tests.testmodels.Event.participants": {
                        "title": "tests.testmodels.Event.participants",
                        "description": "Team that is a playing",
                        "type": "object",
                        "properties": {
                            "id": {
                                "title": "Id",
                                "minimum": 1,
                                "maximum": 2147483647,
                                "type": "integer",
                            },
                            "name": {"title": "Name", "type": "string"},
                            "alias": {
                                "title": "Alias",
                                "minimum": -2147483648,
                                "maximum": 2147483647,
                                "nullable": True,
                                "type": "integer",
                            },
                        },
                        "required": ["id", "name"],
                        "additionalProperties": False,
                    },
                    "tests.testmodels.Event.address": {
                        "title": "tests.testmodels.Event.address",
                        "type": "object",
                        "properties": {
                            "city": {"title": "City", "maxLength": 64, "type": "string"},
                            "street": {"title": "Street", "maxLength": 128, "type": "string"},
                            "event_id": {
                                "title": "Event Id",
                                "minimum": 1,
                                "maximum": 9223372036854775807,
                                "type": "integer",
                            },
                        },
                        "required": ["city", "street", "event_id"],
                        "additionalProperties": False,
                    },
                },
            },
        )

    def test_eventlist_schema(self):
        print(self.Event_Pydantic_List.schema())
        self.assertEqual(
            self.Event_Pydantic_List.schema(),
            {
                "title": "Event_list",
                "description": "Events on the calendar",
                "type": "array",
                "items": {"$ref": "#/definitions/tests.testmodels.Event"},
                "definitions": {
                    "tests.testmodels.Event.tournament": {
                        "title": "tests.testmodels.Event.tournament",
                        "type": "object",
                        "properties": {
                            "id": {
                                "title": "Id",
                                "minimum": 1,
                                "maximum": 32767,
                                "type": "integer",
                            },
                            "name": {"title": "Name", "maxLength": 255, "type": "string"},
                            "desc": {"title": "Desc", "nullable": True, "type": "string"},
                            "created": {
                                "title": "Created",
                                "readOnly": True,
                                "type": "string",
                                "format": "date-time",
                            },
                        },
                        "required": ["id", "name", "created"],
                        "additionalProperties": False,
                    },
                    "tests.testmodels.Event.reporter": {
                        "title": "tests.testmodels.Event.reporter",
                        "description": "Whom is assigned as the reporter",
                        "type": "object",
                        "properties": {
                            "id": {
                                "title": "Id",
                                "minimum": 1,
                                "maximum": 2147483647,
                                "type": "integer",
                            },
                            "name": {"title": "Name", "type": "string"},
                        },
                        "required": ["id", "name"],
                        "additionalProperties": False,
                    },
                    "tests.testmodels.Event.participants": {
                        "title": "tests.testmodels.Event.participants",
                        "description": "Team that is a playing",
                        "type": "object",
                        "properties": {
                            "id": {
                                "title": "Id",
                                "minimum": 1,
                                "maximum": 2147483647,
                                "type": "integer",
                            },
                            "name": {"title": "Name", "type": "string"},
                            "alias": {
                                "title": "Alias",
                                "minimum": -2147483648,
                                "maximum": 2147483647,
                                "nullable": True,
                                "type": "integer",
                            },
                        },
                        "required": ["id", "name"],
                        "additionalProperties": False,
                    },
                    "tests.testmodels.Event.address": {
                        "title": "tests.testmodels.Event.address",
                        "type": "object",
                        "properties": {
                            "city": {"title": "City", "maxLength": 64, "type": "string"},
                            "street": {"title": "Street", "maxLength": 128, "type": "string"},
                            "event_id": {
                                "title": "Event Id",
                                "minimum": 1,
                                "maximum": 9223372036854775807,
                                "type": "integer",
                            },
                        },
                        "required": ["city", "street", "event_id"],
                        "additionalProperties": False,
                    },
                    "tests.testmodels.Event": {
                        "title": "Event",
                        "description": "Events on the calendar",
                        "type": "object",
                        "properties": {
                            "event_id": {
                                "title": "Event Id",
                                "minimum": 1,
                                "maximum": 9223372036854775807,
                                "type": "integer",
                            },
                            "name": {"title": "Name", "description": "The name", "type": "string"},
                            "tournament": {
                                "title": "Tournament",
                                "allOf": [
                                    {"$ref": "#/definitions/tests.testmodels.Event.tournament"}
                                ],
                            },
                            "reporter": {
                                "title": "Reporter",
                                "nullable": True,
                                "allOf": [
                                    {"$ref": "#/definitions/tests.testmodels.Event.reporter"}
                                ],
                            },
                            "participants": {
                                "title": "Participants",
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/tests.testmodels.Event.participants"
                                },
                            },
                            "modified": {
                                "title": "Modified",
                                "readOnly": True,
                                "type": "string",
                                "format": "date-time",
                            },
                            "token": {"title": "Token", "type": "string"},
                            "alias": {
                                "title": "Alias",
                                "minimum": -2147483648,
                                "maximum": 2147483647,
                                "nullable": True,
                                "type": "integer",
                            },
                            "address": {
                                "title": "Address",
                                "nullable": True,
                                "allOf": [{"$ref": "#/definitions/tests.testmodels.Event.address"}],
                            },
                        },
                        "required": ["event_id", "name", "tournament", "participants", "modified"],
                        "additionalProperties": False,
                    },
                },
            },
        )

    async def test_eventlist(self):
        eventlp = await self.Event_Pydantic_List.from_queryset(Event.all())
        # print(eventlp.json(indent=4))
        eventldict = eventlp.dict()["__root__"]

        # Remove timestamps
        del eventldict[0]["modified"]
        del eventldict[0]["tournament"]["created"]
        del eventldict[1]["modified"]
        del eventldict[1]["tournament"]["created"]

        self.assertEqual(
            eventldict,
            [
                {
                    "event_id": self.event.event_id,
                    "name": "Test",
                    # "modified": "2020-01-28T10:43:50.901562",
                    "token": self.event.token,
                    "alias": None,
                    "tournament": {
                        "id": self.tournament.id,
                        "name": "New Tournament",
                        "desc": None,
                        # "created": "2020-01-28T10:43:50.900664"
                    },
                    "reporter": {"id": self.reporter.id, "name": "The Reporter"},
                    "participants": [
                        {"id": self.team1.id, "name": "Onesies", "alias": None},
                        {"id": self.team2.id, "name": "T-Shirts", "alias": None},
                    ],
                    "address": {
                        "event_id": self.address.pk,
                        "city": "Santa Monica",
                        "street": "Ocean",
                    },
                },
                {
                    "event_id": self.event2.event_id,
                    "name": "Test2",
                    # "modified": "2020-01-28T10:43:50.901562",
                    "token": self.event2.token,
                    "alias": None,
                    "tournament": {
                        "id": self.tournament.id,
                        "name": "New Tournament",
                        "desc": None,
                        # "created": "2020-01-28T10:43:50.900664"
                    },
                    "reporter": None,
                    "participants": [
                        {"id": self.team1.id, "name": "Onesies", "alias": None},
                        {"id": self.team2.id, "name": "T-Shirts", "alias": None},
                    ],
                    "address": None,
                },
            ],
        )

    async def test_event(self):
        eventp = await self.Event_Pydantic.from_tortoise_orm(await Event.get(name="Test"))
        # print(eventp.json(indent=4))
        eventdict = eventp.dict()

        # Remove timestamps
        del eventdict["modified"]
        del eventdict["tournament"]["created"]

        self.assertEqual(
            eventdict,
            {
                "event_id": self.event.event_id,
                "name": "Test",
                # "modified": "2020-01-28T10:43:50.901562",
                "token": self.event.token,
                "alias": None,
                "tournament": {
                    "id": self.tournament.id,
                    "name": "New Tournament",
                    "desc": None,
                    # "created": "2020-01-28T10:43:50.900664"
                },
                "reporter": {"id": self.reporter.id, "name": "The Reporter"},
                "participants": [
                    {"id": self.team1.id, "name": "Onesies", "alias": None},
                    {"id": self.team2.id, "name": "T-Shirts", "alias": None},
                ],
                "address": {"event_id": self.address.pk, "city": "Santa Monica", "street": "Ocean"},
            },
        )

    async def test_address(self):
        addressp = await self.Address_Pydantic.from_tortoise_orm(await Address.get(street="Ocean"))
        # print(addressp.json(indent=4))
        addressdict = addressp.dict()

        # Remove timestamps
        del addressdict["event"]["tournament"]["created"]
        del addressdict["event"]["modified"]

        self.assertEqual(
            addressdict,
            {
                "city": "Santa Monica",
                "street": "Ocean",
                "event": {
                    "event_id": self.event.event_id,
                    "name": "Test",
                    "tournament": {
                        "id": self.tournament.id,
                        "name": "New Tournament",
                        "desc": None,
                    },
                    "reporter": {"id": self.reporter.id, "name": "The Reporter"},
                    "participants": [
                        {"id": self.team1.id, "name": "Onesies", "alias": None},
                        {"id": self.team2.id, "name": "T-Shirts", "alias": None},
                    ],
                    "token": self.event.token,
                    "alias": None,
                },
                "event_id": self.address.event_id,
            },
        )

    async def test_tournament(self):
        tournamentp = await self.Tournament_Pydantic.from_tortoise_orm(
            await Tournament.all().first()
        )
        # print(tournamentp.json(indent=4))
        tournamentdict = tournamentp.dict()

        # Remove timestamps
        del tournamentdict["events"][0]["modified"]
        del tournamentdict["events"][1]["modified"]
        del tournamentdict["created"]

        self.assertEqual(
            tournamentdict,
            {
                "id": self.tournament.id,
                "name": "New Tournament",
                "desc": None,
                # "created": "2020-01-28T19:41:38.059617",
                "events": [
                    {
                        "event_id": self.event.event_id,
                        "name": "Test",
                        # "modified": "2020-01-28T19:41:38.060070",
                        "token": self.event.token,
                        "alias": None,
                        "reporter": {"id": self.reporter.id, "name": "The Reporter"},
                        "participants": [
                            {"id": self.team1.id, "name": "Onesies", "alias": None},
                            {"id": self.team2.id, "name": "T-Shirts", "alias": None},
                        ],
                        "address": {
                            "event_id": self.address.pk,
                            "city": "Santa Monica",
                            "street": "Ocean",
                        },
                    },
                    {
                        "event_id": self.event2.event_id,
                        "name": "Test2",
                        # "modified": "2020-01-28T19:41:38.060070",
                        "token": self.event2.token,
                        "alias": None,
                        "reporter": None,
                        "participants": [
                            {"id": self.team1.id, "name": "Onesies", "alias": None},
                            {"id": self.team2.id, "name": "T-Shirts", "alias": None},
                        ],
                        "address": None,
                    },
                ],
            },
        )

    async def test_team(self):
        teamp = await self.Team_Pydantic.from_tortoise_orm(await Team.get(id=self.team1.id))
        # print(teamp.json(indent=4))
        teamdict = teamp.dict()

        # Remove timestamps
        del teamdict["events"][0]["modified"]
        del teamdict["events"][0]["tournament"]["created"]
        del teamdict["events"][1]["modified"]
        del teamdict["events"][1]["tournament"]["created"]

        self.assertEqual(
            teamdict,
            {
                "id": self.team1.id,
                "name": "Onesies",
                "alias": None,
                "events": [
                    {
                        "event_id": self.event.event_id,
                        "name": "Test",
                        # "modified": "2020-01-28T19:47:03.334077",
                        "token": self.event.token,
                        "alias": None,
                        "tournament": {
                            "id": self.tournament.id,
                            "name": "New Tournament",
                            "desc": None,
                            # "created": "2020-01-28T19:41:38.059617",
                        },
                        "reporter": {"id": self.reporter.id, "name": "The Reporter"},
                        "address": {
                            "event_id": self.address.pk,
                            "city": "Santa Monica",
                            "street": "Ocean",
                        },
                    },
                    {
                        "event_id": self.event2.event_id,
                        "name": "Test2",
                        # "modified": "2020-01-28T19:47:03.334077",
                        "token": self.event2.token,
                        "alias": None,
                        "tournament": {
                            "id": self.tournament.id,
                            "name": "New Tournament",
                            "desc": None,
                            # "created": "2020-01-28T19:41:38.059617",
                        },
                        "reporter": None,
                        "address": None,
                    },
                ],
            },
        )

    async def test_depth(self):
        team2_pydantic = pydantic_model_creator(Team, name="Team2", depth=3).schema()
        self.assertEqual(
            team2_pydantic,
            {
                "title": "Team2",
                "description": "Team that is a playing",
                "type": "object",
                "properties": {
                    "id": {"title": "Id", "minimum": 1, "maximum": 2147483647, "type": "integer"},
                    "name": {"title": "Name", "type": "string"},
                    "alias": {
                        "title": "Alias",
                        "minimum": -2147483648,
                        "maximum": 2147483647,
                        "nullable": True,
                        "type": "integer",
                    },
                    "events": {
                        "title": "Events",
                        "type": "array",
                        "items": {"$ref": "#/definitions/Team2.events"},
                    },
                },
                "required": ["id", "name", "events"],
                "additionalProperties": False,
                "definitions": {
                    "Team2.events.tournament": {
                        "title": "Team2.events.tournament",
                        "type": "object",
                        "properties": {
                            "id": {
                                "title": "Id",
                                "minimum": 1,
                                "maximum": 32767,
                                "type": "integer",
                            },
                            "name": {"title": "Name", "maxLength": 255, "type": "string"},
                            "desc": {"title": "Desc", "nullable": True, "type": "string"},
                            "created": {
                                "title": "Created",
                                "readOnly": True,
                                "type": "string",
                                "format": "date-time",
                            },
                        },
                        "required": ["id", "name", "created"],
                        "additionalProperties": False,
                    },
                    "Team2.events.reporter": {
                        "title": "Team2.events.reporter",
                        "description": "Whom is assigned as the reporter",
                        "type": "object",
                        "properties": {
                            "id": {
                                "title": "Id",
                                "minimum": 1,
                                "maximum": 2147483647,
                                "type": "integer",
                            },
                            "name": {"title": "Name", "type": "string"},
                        },
                        "required": ["id", "name"],
                        "additionalProperties": False,
                    },
                    "Team2.events.address": {
                        "title": "Team2.events.address",
                        "type": "object",
                        "properties": {
                            "city": {"title": "City", "maxLength": 64, "type": "string"},
                            "street": {"title": "Street", "maxLength": 128, "type": "string"},
                            "event_id": {
                                "title": "Event Id",
                                "minimum": 1,
                                "maximum": 9223372036854775807,
                                "type": "integer",
                            },
                        },
                        "required": ["city", "street", "event_id"],
                        "additionalProperties": False,
                    },
                    "Team2.events": {
                        "title": "Team2.events",
                        "description": "Events on the calendar",
                        "type": "object",
                        "properties": {
                            "event_id": {
                                "title": "Event Id",
                                "minimum": 1,
                                "maximum": 9223372036854775807,
                                "type": "integer",
                            },
                            "name": {"title": "Name", "description": "The name", "type": "string"},
                            "tournament": {
                                "title": "Tournament",
                                "allOf": [{"$ref": "#/definitions/Team2.events.tournament"}],
                            },
                            "reporter": {
                                "title": "Reporter",
                                "nullable": True,
                                "allOf": [{"$ref": "#/definitions/Team2.events.reporter"}],
                            },
                            "modified": {
                                "title": "Modified",
                                "readOnly": True,
                                "type": "string",
                                "format": "date-time",
                            },
                            "token": {"title": "Token", "type": "string"},
                            "alias": {
                                "title": "Alias",
                                "minimum": -2147483648,
                                "maximum": 2147483647,
                                "nullable": True,
                                "type": "integer",
                            },
                            "address": {
                                "title": "Address",
                                "nullable": True,
                                "allOf": [{"$ref": "#/definitions/Team2.events.address"}],
                            },
                        },
                        "required": ["event_id", "name", "tournament", "modified"],
                        "additionalProperties": False,
                    },
                },
            },
        )
        team3_pydantic = pydantic_model_creator(Team, name="Team3", depth=2).schema()
        self.assertEqual(
            team3_pydantic,
            {
                "title": "Team3",
                "description": "Team that is a playing",
                "type": "object",
                "properties": {
                    "id": {"title": "Id", "minimum": 1, "maximum": 2147483647, "type": "integer"},
                    "name": {"title": "Name", "type": "string"},
                    "alias": {
                        "title": "Alias",
                        "minimum": -2147483648,
                        "maximum": 2147483647,
                        "nullable": True,
                        "type": "integer",
                    },
                    "events": {
                        "title": "Events",
                        "type": "array",
                        "items": {"$ref": "#/definitions/Team3.events"},
                    },
                },
                "required": ["id", "name", "events"],
                "additionalProperties": False,
                "definitions": {
                    "Team3.events": {
                        "title": "Team3.events",
                        "description": "Events on the calendar",
                        "type": "object",
                        "properties": {
                            "event_id": {
                                "title": "Event Id",
                                "minimum": 1,
                                "maximum": 9223372036854775807,
                                "type": "integer",
                            },
                            "name": {"title": "Name", "description": "The name", "type": "string"},
                            "modified": {
                                "title": "Modified",
                                "readOnly": True,
                                "type": "string",
                                "format": "date-time",
                            },
                            "token": {"title": "Token", "type": "string"},
                            "alias": {
                                "title": "Alias",
                                "minimum": -2147483648,
                                "maximum": 2147483647,
                                "nullable": True,
                                "type": "integer",
                            },
                        },
                        "required": ["event_id", "name", "modified"],
                        "additionalProperties": False,
                    }
                },
            },
        )

    def test_event_named(self):
        Event_Named = pydantic_model_creator(Event, name="Foo")
        schema = Event_Named.schema()
        self.assertEqual(schema["title"], "Foo")
        self.assertSetEqual(
            set(schema["properties"].keys()),
            {
                "address",
                "alias",
                "event_id",
                "modified",
                "name",
                "participants",
                "reporter",
                "token",
                "tournament",
            },
        )

    def test_event_sorted(self):
        Event_Named = pydantic_model_creator(Event, sort_alphabetically=True)
        schema = Event_Named.schema()
        self.assertEqual(
            list(schema["properties"].keys()),
            [
                "address",
                "alias",
                "event_id",
                "modified",
                "name",
                "participants",
                "reporter",
                "token",
                "tournament",
            ],
        )

    def test_event_unsorted(self):
        Event_Named = pydantic_model_creator(Event, sort_alphabetically=False)
        schema = Event_Named.schema()
        self.assertEqual(
            list(schema["properties"].keys()),
            [
                "event_id",
                "name",
                "tournament",
                "reporter",
                "participants",
                "modified",
                "token",
                "alias",
                "address",
            ],
        )
