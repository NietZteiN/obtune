import std.math;
import std.typecons;
import std.string;
import std.conv;

string f(string text, string prefix) 
{
    if (text.startsWith(prefix))
    {
        text = text[prefix.length .. $];
    }
    text = text.capitalize();
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("qdhstudentamxupuihbuztn", "jdm") == "Qdhstudentamxupuihbuztn");
}
void main(){}
