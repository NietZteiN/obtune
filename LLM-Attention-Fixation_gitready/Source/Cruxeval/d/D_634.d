import std.math;
import std.typecons;
import std.algorithm;
import std.string;

string f(string input_string) 
{
    while (input_string.canFind('a') || input_string.canFind('A'))
    {
        input_string = input_string.replace("a", "i").replace("A", "i");
        input_string = input_string.replace("i", "o").replace("I", "O");
        input_string = input_string.replace("o", "u").replace("O", "U");
        input_string = input_string.replace("u", "a").replace("U", "A");
    }
    return input_string;
}
unittest
{
    alias candidate = f;

    assert(candidate("biec") == "biec");
}
void main(){}
