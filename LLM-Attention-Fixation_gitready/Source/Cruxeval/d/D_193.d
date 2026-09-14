import std.math;
import std.typecons;
import std.algorithm;
import std.array;

string f(string s) 
{
    size_t count = s.count(":");
    auto parts = s.split(":");
    return parts[0..$-2].join(":") ~ ":" ~ parts[$-1];
}
unittest
{
    alias candidate = f;

    assert(candidate("1::1") == "1:1");
}
void main(){}
