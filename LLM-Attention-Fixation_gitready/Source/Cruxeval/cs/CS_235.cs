using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<string> array, List<string> arr) {
        List<string> result = new List<string>();
        foreach(string s in arr)
        {
            result.AddRange(s.Split(new string[] { arr[array.IndexOf(s)] }, StringSplitOptions.RemoveEmptyEntries).ToList());
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>()), (new List<string>())).SequenceEqual((new List<string>())));
    }

}
