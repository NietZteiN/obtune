import std.math;
import std.typecons;
import std.string;

string f(string text, string prefix) {
    if (!text.empty) {
        if (text.startsWith(prefix)) {
            text = text[prefix.length .. $];
        }
        if (!text.empty) {
            text = text[0 .. $-1] ~ text[$-1 .. $].toUpper();
        }
    }
    return text;
}

unittest
{
    alias candidate = f;

    assert(candidate("querist", "u") == "querisT");
}
void main(){}
