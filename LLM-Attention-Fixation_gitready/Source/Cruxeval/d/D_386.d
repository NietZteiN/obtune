import std.math;
import std.typecons;
import std.algorithm;
import std.array;

string f(string concat, Nullable!(string[string]) di) 
{
    if (!di.isNull) {
        auto arr = di.get.keys.array;
        arr.sort();
        foreach (i; 0 .. arr.length) {
            if (concat.canFind(di.get[arr[i]])) {
                di.get.remove(arr[i]);
            }
        }
    }
    return "Done!";
}
unittest
{
    alias candidate = f;

    assert(candidate("mid", ["0": "q", "1": "f", "2": "w", "3": "i"].nullable) == "Done!");
}
void main(){}
