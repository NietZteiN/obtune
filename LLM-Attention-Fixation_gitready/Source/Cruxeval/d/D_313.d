import std.math;
import std.typecons;
import std.string;

string f(string s, long l) 
{
    return (s.length <= l) ? s : s[0 .. ((s.length-l).abs)] ;
}
unittest
{
    alias candidate = f;

    assert(candidate("urecord", 8L) == "urecord");
}
void main(){}
