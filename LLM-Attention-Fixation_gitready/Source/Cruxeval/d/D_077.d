import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.array;

string f(string text, string character) 
{
    auto idx = text.lastIndexOf(character);
    if (idx == -1) {
        return "";
    }
    auto subject = text[idx .. $];
    return subject.replicate(text.count(character));
}

unittest
{
    alias candidate = f;

    assert(candidate("h ,lpvvkohh,u", "i") == "");
}
void main(){}
