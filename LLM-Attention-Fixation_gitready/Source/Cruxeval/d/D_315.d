import std.math;
import std.typecons;
import std.string;
string f(string challenge) 
{
    return challenge.toLower().replace("l", ",");
}
unittest
{
    alias candidate = f;

    assert(candidate("czywZ") == "czywz");
}
void main(){}
