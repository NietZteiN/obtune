using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<string> values) {
        List<string> names = new List<string>() { "Pete", "Linda", "Angela" };
        names.AddRange(values);
        names.Sort();
        return names;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"Dan", (string)"Joe", (string)"Dusty"}))).SequenceEqual((new List<string>(new string[]{(string)"Angela", (string)"Dan", (string)"Dusty", (string)"Joe", (string)"Linda", (string)"Pete"}))));
    }

}
