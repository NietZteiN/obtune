import std.math;
import std.typecons;
import std.string;

Tuple!(string, string) f(string text) {
    auto parts = text.split("|");
    string topic, problem;
    if (parts.length > 1) {
        topic = parts[0 .. $-1].join("|");
        problem = parts[$-1];
    } else {
        topic = "";
        problem = parts[0];
    }
    if (problem == "r") {
        problem = topic.replace("u", "p");
    }
    return tuple(topic, problem);
}

unittest
{
    alias candidate = f;

    assert(candidate("|xduaisf") == tuple("", "xduaisf"));
}
void main(){}
