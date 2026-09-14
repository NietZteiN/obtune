import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string[] array) 
{
    if (array.length == 1) {
        return array[0];
    }
    auto result = array.dup;
    size_t i = 0;
    while (i < array.length - 1) {
        foreach (j; 0..2) {
            result[i * 2] = array[i];
            i++;
        }
    }
    return result.join("");
}
unittest
{
    alias candidate = f;

    assert(candidate(["ac8", "qk6", "9wg"]) == "ac8qk6qk6");
}
void main(){}
