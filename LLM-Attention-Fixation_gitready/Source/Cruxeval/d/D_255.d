import std.math;
import std.typecons;
import std.string;

string f(string text, string fill, long size) 
{
    if (size < 0) {
        size = -size;
    }
    if (text.length > size) {
        return text[text.length - size .. $];
    }
    return format("%*s", size, text);
}
unittest
{
    alias candidate = f;

    assert(candidate("no asw", "j", 1L) == "w");
}
void main(){}
