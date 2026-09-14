using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(List<string> array) {
        if (array.Count == 1)
        {
            return string.Join("", array);
        }
        var result = new List<string>(array);
        int i = 0;
        while (i < array.Count - 1)
        {
            for (int j = 0; j < 2; j++)
            {
                result[i * 2] = array[i];
                i += 1;
            }
        }
        return string.Join("", result);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"ac8", (string)"qk6", (string)"9wg"}))).Equals(("ac8qk6qk6")));
    }

}
