import std.math;
import std.typecons;
import std.string;

string f(string a) 
{
    return a.split().join(" ");
}
unittest
{
    alias candidate = f;

    assert(candidate(" h e l l o   w o r l d! ") == "h e l l o w o r l d!");
}
void main(){}
