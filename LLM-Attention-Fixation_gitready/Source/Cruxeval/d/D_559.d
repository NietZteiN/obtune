import std.math;
import std.typecons;
import std.string;

string f(string n) 
{
    return n[0] ~ ('.' ~ n[1..$].replace("-", "_"));
}
unittest
{
    alias candidate = f;

    assert(candidate("first-second-third") == "f.irst_second_third");
}
void main(){}
