import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.range;
import std.string;

long f(string text) 
{
    long result = -1;
    foreach (ch; "aeiou") {
        auto index = text.indexOf(ch);
        if (index > result) {
            result = index;
        }
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("qsqgijwmmhbchoj") == 13L);
}
void main(){}
