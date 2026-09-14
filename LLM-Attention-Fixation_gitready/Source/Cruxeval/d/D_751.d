import std.math;
import std.typecons;
import std.string;
string f(string text, string character, long min_count) 
{
    long count = text.count(character);
    if (count < min_count) {
        return text.toUpper();
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("wwwwhhhtttpp", "w", 3L) == "wwwwhhhtttpp");
}
void main(){}
