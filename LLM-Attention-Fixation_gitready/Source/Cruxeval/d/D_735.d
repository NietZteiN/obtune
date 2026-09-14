import std.math;
import std.typecons;
import std.string;

string f(string sentence) 
{
    if (sentence.empty)
    {
        return "";
    }
    sentence = sentence.replace("(", "");
    sentence = sentence.replace(")", "");
    sentence = sentence.capitalize;
    sentence = sentence.replace(" ", "");
    return sentence;
}
unittest
{
    alias candidate = f;

    assert(candidate("(A (b B))") == "Abb");
}
void main(){}
