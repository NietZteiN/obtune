import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string name) 
{
    return "| " ~ name.split(" ").join(" ") ~ " |";
}
unittest
{
    alias candidate = f;

    assert(candidate("i am your father") == "| i am your father |");
}
void main(){}
