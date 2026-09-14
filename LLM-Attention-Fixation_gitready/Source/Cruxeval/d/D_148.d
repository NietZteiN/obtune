import std.math;
import std.typecons;
import std.string;

string f(string forest, string animal) 
{
    auto result = cast(char[])forest.dup;
    auto index = forest.indexOf(animal);
    while (index < forest.length - 1) 
    {
        result[index] = forest[index + 1];
        index++;
    }
    if (index == forest.length - 1) 
    {
        result[index] = '-';
    }
    return result.idup;
}
unittest
{
    alias candidate = f;

    assert(candidate("2imo 12 tfiqr.", "m") == "2io 12 tfiqr.-");
}
void main(){}
