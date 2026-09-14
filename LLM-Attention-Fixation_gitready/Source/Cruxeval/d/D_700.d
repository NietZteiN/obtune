import std.math;
import std.typecons;
import std.algorithm;
import std.range;
import std.string;

long f(string text) 
{
    return text.length - text.count("bot");
}
unittest
{
    alias candidate = f;

    assert(candidate("Where is the bot in this world?") == 30L);
}
void main(){}
