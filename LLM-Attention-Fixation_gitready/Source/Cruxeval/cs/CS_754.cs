using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<string> nums) {
        if (nums.Count == 0)
        {
            return new List<string>();
        }
        int width = int.Parse(nums[0]);
        return nums.Skip(1).Select(val => val.PadLeft(width, '0')).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"1", (string)"2", (string)"2", (string)"44", (string)"0", (string)"7", (string)"20257"}))).SequenceEqual((new List<string>(new string[]{(string)"2", (string)"2", (string)"44", (string)"0", (string)"7", (string)"20257"}))));
    }

}
