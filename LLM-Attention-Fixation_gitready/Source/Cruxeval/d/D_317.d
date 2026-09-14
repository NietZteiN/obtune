import std.math;
import std.typecons;
import std.string;

string f(string text, string a, string b) 
{
    string new_text = text.replace(a, b);
    return new_text.replace(b, a);
}
unittest
{
    alias candidate = f;

    assert(candidate(" vup a zwwo oihee amuwuuw! ", "a", "u") == " vap a zwwo oihee amawaaw! ");
}
void main(){}
