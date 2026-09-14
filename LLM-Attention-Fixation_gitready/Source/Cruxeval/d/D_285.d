import std.math;
import std.typecons;
import std.string;

long f(string text, string ch) 
{
    return text.count(ch);
}
unittest
{
    alias candidate = f;

    assert(candidate("This be Pirate's Speak for 'help'!", " ") == 5L);
}
void main(){}
