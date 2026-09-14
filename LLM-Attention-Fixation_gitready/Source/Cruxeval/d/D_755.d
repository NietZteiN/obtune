import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string replace, string text, string hide) 
{
    while (text.canFind(hide))
    {
        replace ~= "ax";
        text = text.replaceFirst(hide, replace);
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("###", "ph>t#A#BiEcDefW#ON#iiNCU", ".") == "ph>t#A#BiEcDefW#ON#iiNCU");
}
void main(){}
