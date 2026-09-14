import std.math;
import std.typecons;
string f(string text) 
{
    return text[$-1] ~ text[0 .. $-1];
}
unittest
{
    alias candidate = f;

    assert(candidate("hellomyfriendear") == "rhellomyfriendea");
}
void main(){}
