defmodule TaskPackCreator do
  import Ecto.Query


  @names  [
  "double_letters",
  "compress_repeats",
  "sum_numbers_in_text",
  "uncompress_repeats",
  "typed_string_equality",
  "bike_to_charge",
  "overlapping_intervals",
  "log_ip_sanitizer",
  ]

  def run do
    query = from(t in Codebattle.Task, where: t.name in ^@names)
    tasks = Codebattle.Repo.all(query)
    tasks_by_name = Map.new(tasks, &{&1.name, &1})
    ids = Enum.map(@names, fn name -> tasks_by_name[name].id end)

    task_pack = %Codebattle.TaskPack{
      name: "masters_s0_2025_2",
      state: "active",
      visibility: "hidden",
      task_ids: ids,
      creator_id: 1
    }

    Codebattle.Repo.insert(task_pack)
  end

end
TaskPackCreator.run()
