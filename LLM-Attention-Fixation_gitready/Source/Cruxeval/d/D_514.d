import std.math;
import std.typecons;
import std.array;
import std.algorithm;

string f(string text) 
{
    foreach (word; text.split())
    {
        text = text.replace("-" ~ word, " ").replace(word ~ "-", " ");
    }
    return text.stripLeft('-').stripRight('-');
}
unittest
{
    alias candidate = f;

    assert(candidate("-stew---corn-and-beans-in soup-.-") == "stew---corn-and-beans-in soup-.");
}
void main(){}
