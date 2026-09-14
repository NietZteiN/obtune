import std.math;
import std.typecons;
import std.range;

string f(string s) 
{
    return s[3..$] ~ s[2] ~ s[5..$];
}
unittest
{
    alias candidate = f;

    assert(candidate("jbucwc") == "cwcuc");
}
void main(){}
