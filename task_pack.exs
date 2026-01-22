defmodule TaskPackCreator do
  import Ecto.Query

  @names [
    "clue_intersection",
    "squad_split",
    "secret_lab_shift_hours",
    "eggo_boxes_needed",
    "walkie_talkie_range",
    "christmas_lights_groups",
    "demogorgon_alert",
    "portal_sightings_sum",
    "hawkins_missing",
    "upside_down_label",
    "episode_binge_min",
    "lab_patrol_coverage"
  ]

  def run do
    query = from(t in Codebattle.Task, where: t.name in ^@names)
    tasks = Codebattle.Repo.all(query)
    tasks_by_name = Map.new(tasks, &{&1.name, &1})
    ids = Enum.map(@names, fn name -> tasks_by_name[name].id end)

    task_pack = %Codebattle.TaskPack{
      name: "masters_s0_2026_1",
      state: "active",
      visibility: "hidden",
      task_ids: ids,
      creator_id: 1
    }

    Codebattle.Repo.insert(task_pack)
  end
end

TaskPackCreator.run()
