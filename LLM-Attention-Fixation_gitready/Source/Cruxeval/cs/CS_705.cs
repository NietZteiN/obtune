using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<string> cities, string name) {
        if (string.IsNullOrEmpty(name)) {
            return cities;
        }
        if (name != "cities") {
            return new List<string>();
        }
        return cities.Select(city => name + city).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"Sydney", (string)"Hong Kong", (string)"Melbourne", (string)"Sao Paolo", (string)"Istanbul", (string)"Boston"})), ("Somewhere ")).SequenceEqual((new List<string>())));
    }

}
