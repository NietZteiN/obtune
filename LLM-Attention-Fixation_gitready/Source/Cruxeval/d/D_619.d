import std.math;
import std.typecons;
import std.string;

string f(string title) 
{
    return toLower(title);
}
unittest
{
    alias candidate = f;

    assert(candidate("   Rock   Paper   SCISSORS  ") == "   rock   paper   scissors  ");
}
void main(){}
