using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<long> array) {
        var just_ns = array.Select(num => new String('n', (int)num)).ToList();
        var final_output = new List<string>();
        foreach(var wipe in just_ns)
        {
            final_output.Add(wipe);
        }
        return final_output;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>())).SequenceEqual((new List<string>())));
    }

}
