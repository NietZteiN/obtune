import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

long f(string text, string search) 
{
    auto result = text.toLower();
    return result.indexOf(search.toLower());
}
unittest
{
    alias candidate = f;

    assert(candidate("car hat", "car") == 0L);
}
void main(){}
