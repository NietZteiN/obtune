import std.math;
import std.typecons;

Nullable!(string[string]) f(string[] arr, Nullable!(string[string]) d)
{
    if (d.isNull) {
        d = new string[string];
    }
    for (int i = 1; i < arr.length; i += 2) {
        d.get[arr[i]] = arr[i-1];
    }
    return d;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate(["b", "vzjmc", "f", "ae", "0"], Nullable!(string[string]).init);
        assert(!result.isNull && result.get == ["vzjmc": "b", "ae": "f"]);
}

}
void main(){}
