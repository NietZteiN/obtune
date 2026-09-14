import std.string;
import std.algorithm;
import std.typecons;

string f(string text) {
    if (text.canFind(',')) {
        auto parts = text.split(",");
        return parts[1 .. $].join(",") ~ " " ~ parts[0];
    }
    auto parts = text.split(" ");
    return "," ~ (parts.length > 1 ? parts[1 .. $].join(" ") : "") ~ " 0";
}

unittest
{
    alias candidate = f;

    assert(candidate("244, 105, -90") == " 105, -90 244");
}
void main(){}
