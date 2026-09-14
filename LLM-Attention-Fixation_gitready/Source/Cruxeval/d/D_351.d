import std.math;
import std.typecons;
import std.algorithm;
import std.array;

string f(string text) 
{
    scope(exit) text = text.replace("nnet lloP", "nnet loLp");
    return text;
}

unittest
{
    alias candidate = f;

    assert(candidate("a_A_b_B3 ") == "a_A_b_B3 ");
}
void main(){}
