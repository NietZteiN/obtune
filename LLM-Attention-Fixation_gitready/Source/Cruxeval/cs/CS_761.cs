using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array) {
        var output = new List<long>(array);
        for (int i = 0; i < output.Count; i+=2)
        {
            output[i] = output[output.Count - 1 - i];
        }
        output.Reverse();
        return output;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>())).SequenceEqual((new List<long>())));
    }

}
