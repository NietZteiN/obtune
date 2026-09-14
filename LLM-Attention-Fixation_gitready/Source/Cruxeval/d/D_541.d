import std.math;
import std.typecons;
import std.string;
bool f(string text) 
{
    return text.strip().length == 0;
}
unittest
{
    alias candidate = f;

    assert(candidate(" 	  　") == true);
}
void main(){}
