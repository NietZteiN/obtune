import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string[][] messages) 
{
    string phone_code = "+353";
    string[] result;
    foreach (message; messages)
    {
        message ~= phone_code.split("");
        result ~= message.join(";");
    }
    return result.join(". ");
}
unittest
{
    alias candidate = f;

    assert(candidate([["Marie", "Nelson", "Oscar"]]) == "Marie;Nelson;Oscar;+;3;5;3");
}
void main(){}
