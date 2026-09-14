import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.array;

string f(string name) 
{
    string new_name = "";
    name = name.dup.reverse; // create a reversed copy of the string
    foreach (i, n; name)
    {
        if (n != '.' && new_name.count('.') < 2)
        {
            new_name = n ~ new_name;
        }
        else
        {
            break;
        }
    }
    return new_name;
}
unittest
{
    alias candidate = f;

    assert(candidate(".NET") == "NET");
}
void main(){}
