import std.math;
import std.typecons;
import std.conv;
import std.range;
import std.string;

string f(long n) 
{
    long t = 0;
    string b = "";
    auto digits = n.text.dup;
    foreach(d; 0 .. digits.length)
    {
        if(digits[d] == '0') t += 1;
        else break;
    }
    foreach(ix; 0 .. t)
        b ~= "104";
    return b ~ n.text;
}
unittest
{
    alias candidate = f;

    assert(candidate(372359L) == "372359");
}
void main(){}
